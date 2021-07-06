#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

#include <gempyre.h>
#include <gempyre_graphics.h>
#include <gempyre_client.h>
#include <gempyre_utils.h>

namespace py = pybind11;


class RectF {
public:
    double x, y, width, height;
    operator Gempyre::Element::Rect() const {
        return Gempyre::Element::Rect{static_cast<int>(x), static_cast<int>(y), static_cast<int>(width), static_cast<int>(height)};
    }
};



static RectF rectF(const Gempyre::Element::Rect& r) {
    return RectF{ static_cast<double>(r.x), static_cast<double>(r.y), static_cast<double>(r.width), static_cast<double>(r.height) };
}


static  std::optional<std::string> GempyreExtension(Gempyre::Ui* ui, const std::string& callId, const std::unordered_map<std::string, std::string>& parameters) {
    std::unordered_map<std::string, std::any> params;
    for(const auto& [k, v] : parameters) {
        const auto any = GempyreUtils::jsonToAny(v); // Not sure how well tested
        if(any)
            params.emplace(k, any);
         else {
            std::cerr << "Cannot make " << k << "->" << v << " to any" << std::endl;
            return std::nullopt;
        }
    }
    std::optional<std::any> ext =  ui->extension(callId, params);
    return ext ? GempyreUtils::toJsonString(*ext) : std::nullopt;
}

static std::string findBrowser() {
    try {
        const auto pyclient_browser = py::module::import("pyclient");
        const auto browser_path = pyclient_browser.attr("__file__");
        const auto browser = browser_path.cast<std::string>();

        if(!GempyreUtils::fileExists(browser))
            return std::string();
    
        const auto sys = py::module::import("sys");
        const auto result = sys.attr("executable");
        return result.cast<std::string>() + " " + browser;
        } catch(...) {}
        return std::string();
}


PYBIND11_MODULE(Gempyre, m) {
    py::enum_<Gempyre::DebugLevel>(m, "DebugLevel")
    .value("Quiet", Gempyre::DebugLevel::Quiet)
    .value("Fatal", Gempyre::DebugLevel::Fatal)
    .value("Error", Gempyre::DebugLevel::Error)
    .value("Warning", Gempyre::DebugLevel::Warning)
    .value("Info", Gempyre::DebugLevel::Info)
    .value("Debug", Gempyre::DebugLevel::Debug)
    .value("Debug_Trace", Gempyre::DebugLevel::Debug_Trace);
    m.def("set_debug", &Gempyre::setDebug, py::arg("level") = Gempyre::DebugLevel::Warning, py::arg("useLog") = false);
    m.def("version", &Gempyre::version);
	m.def("os_browser", &GempyreUtils::osBrowser); //is this the only function fom GempyreUtils? Therefore attached here

    py::class_<Gempyre::Event>(m, "Event")
            .def_readonly("element", &Gempyre::Event::element)
            .def_readonly("properties", &Gempyre::Event::properties)
            ;

    py::class_<RectF>(m, "Rect")
            .def(py::init<>())
            .def(py::init<double, double, double, double>())
            .def_readwrite("x", &RectF::x)
            .def_readwrite("y", &RectF::y)
            .def_readwrite("width", &RectF::width)
            .def_readwrite("height", &RectF::height)
            ;

    py::class_<Gempyre::Element>(m, "Element")
            .def(py::init<const Gempyre::Element&>())
            .def(py::init<Gempyre::Ui&, const std::string&>())
            .def(py::init<Gempyre::Ui&, const std::string, const std::string&, const Gempyre::Element&>())
            .def(py::init<Gempyre::Ui&, const std::string&, const Gempyre::Element&>())
            .def("ui", py::overload_cast<>(&Gempyre::Element::ui, py::const_))
            .def("ui", py::overload_cast<>(&Gempyre::Element::ui))
            .def("id", &Gempyre::Element::id)
            .def("subscribe", [](Gempyre::Element* el, const std::string& name, std::function<void(const Gempyre::Event& ev)> handler, const std::vector<std::string>& properties, const std::chrono::milliseconds& throttle = 0ms) {
                 return el->subscribe(name, [handler](const Gempyre::Event& ev) {
                     py::gil_scoped_acquire acquire; handler(ev);
                 }, properties, throttle);
                }, py::arg("name"), py::arg("handler"), py::arg("properties") = std::vector<std::string>{}, py::arg("throttle") = 0ms)
            .def("set_html", &Gempyre::Element::setHTML)
            .def("set_attribute", &Gempyre::Element::setAttribute, py::arg("attr"), py::arg("value") = "")
            .def("remove_attribute", &Gempyre::Element::removeAttribute)
            .def("set_style", &Gempyre::Element::setStyle)
            .def("remove_style", &Gempyre::Element::removeStyle)
            .def("styles", &Gempyre::Element::styles)
            .def("attributes", &Gempyre::Element::attributes)
            .def("children", &Gempyre::Element::children)
            .def("values", &Gempyre::Element::values)
            .def("html", &Gempyre::Element::html)
            .def("remove", &Gempyre::Element::remove)
            .def("type", &Gempyre::Element::type)
            .def("rect", [](Gempyre::Element* el) {
                const auto r = el->rect();
                return r ? std::make_optional<RectF>(::rectF(*r)) :  std::nullopt;
                })
//            .def("rect", &Gempyre::Element::rect)
            ;
    py::class_<Gempyre::Ui>(m, "Ui")
       // Should I comment these out as using them is confusing due browser security concerns
        .def(py::init<const std::string&, const std::string&, const std::string&, unsigned short, const std::string& >(),
             py::arg("indexHtml"),
             py::arg("browser") = findBrowser(),
             py::arg("extraParams") = "",
             py::arg("port") = Gempyre::Ui::UseDefaultPort,
             py::arg("root") = Gempyre::Ui::UseDefaultRoot
             )
        /*.def(py::init<const std::string&, unsigned short, const std::string& >(),
                 py::arg("indexHtml"),
                 py::arg("port") = Gempyre::Ui::UseDefaultPort,
                 py::arg("root") = Gempyre::Ui::UseDefaultRoot
                 ) */
        .def(py::init<const Gempyre::Ui::Filemap&, const std::string&, const std::string&, const std::string&, unsigned short, const std::string& >(),
             py::arg("filemap"),
             py::arg("indexHtml"),
             py::arg("browser") = findBrowser(),
             py::arg("extraParams") = "",
             py::arg("port") = Gempyre::Ui::UseDefaultPort,
             py::arg("root") = Gempyre::Ui::UseDefaultRoot
             )
        /*.def(py::init<const Gempyre::Ui::Filemap&, const std::string&, unsigned short, const std::string& >(),
             py::arg("filemap"),
             py::arg("indexHtml"),
             py::arg("port") = Gempyre::Ui::UseDefaultPort,
             py::arg("root") = Gempyre::Ui::UseDefaultRoot
            )*/
        .def_readonly_static("UseDefaultPort", &Gempyre::Ui::UseDefaultPort)
        .def_readonly_static("UseDefaultRoot", &Gempyre::Ui::UseDefaultRoot)
        .def("run", &Gempyre::Ui::run, py::call_guard<py::gil_scoped_release>())
        .def("exit", &Gempyre::Ui::exit)
        .def("close", &Gempyre::Ui::close)
        .def("on_exit", [](Gempyre::Ui* ui, std::function<void ()> onExitFunction = nullptr)->Gempyre::Ui& {
            return ui->onExit(onExitFunction ? [onExitFunction]() {
                py::gil_scoped_acquire acquire;
                return onExitFunction();
            } : static_cast<decltype(onExitFunction)>(nullptr));
        })
        .def("on_reload", [](Gempyre::Ui* ui, std::function<void ()> onReloadFunction = nullptr)->Gempyre::Ui& {
        return ui->onReload(onReloadFunction ? [onReloadFunction]() {
            py::gil_scoped_acquire acquire;
            return onReloadFunction();
        } : static_cast<decltype(onReloadFunction)>(nullptr));
        })
        .def("on_open", [](Gempyre::Ui* ui, std::function<void ()> onOpenFunction = nullptr)->Gempyre::Ui& {
        return ui->onOpen(onOpenFunction ? [onOpenFunction]() {
            py::gil_scoped_acquire acquire;
            return onOpenFunction();
        } : static_cast<decltype(onOpenFunction)>(nullptr));
        })
        .def("on_error", [](Gempyre::Ui* ui, std::function<void (const std::string& element, const std::string& info)> onErrorFunction = nullptr)->Gempyre::Ui& {
            return ui->onError(onErrorFunction ? [onErrorFunction](const std::string& element, const std::string& info) {
                py::gil_scoped_acquire acquire;
                return onErrorFunction(element, info);
            } : static_cast<decltype(onErrorFunction)>(nullptr));
        })
        .def("set_logging", &Gempyre::Ui::setLogging)
        .def("eval", &Gempyre::Ui::eval)
        .def("debug", &Gempyre::Ui::debug)
        .def("alert", &Gempyre::Ui::alert)
        .def("open", &Gempyre::Ui::open, py::arg("url"), py::arg("name") = "")
        .def("start_timer", [](Gempyre::Ui* ui, const std::chrono::milliseconds& ms, bool b, const std::function<void ()>& f) {
            return ui->startTimer(ms, b, [f]() {
                py::gil_scoped_acquire acquire;
                f();
            });
        })
        // When wrapping in fp (to enable GIL), there is no need: py::overload_cast<const std::chrono::milliseconds&, bool, const std::function<void (Gempyre::Ui::TimerId)>&>(&Gempyre::Ui::startTimer)
        .def("start_timer_id", [](Gempyre::Ui* ui, const std::chrono::milliseconds& ms, bool b, const std::function<void (Gempyre::Ui::TimerId)>& f) {
            return ui->startTimer(ms, b, [f](Gempyre::Ui::TimerId tid) {
                py::gil_scoped_acquire acquire;
                f(tid);
            });
        })
        .def("stop_timer", &Gempyre::Ui::stopTimer)
        .def("root", &Gempyre::Ui::root)
        .def("address_of", &Gempyre::Ui::addressOf)
        .def("by_class", &Gempyre::Ui::byClass)
        .def("by_name", &Gempyre::Ui::byName)
        .def("ping", &Gempyre::Ui::ping)
         .def("extension", &GempyreExtension)
        .def("resource", &Gempyre::Ui::resource)
        .def("add_file", &Gempyre::Ui::addFile)
        .def("begin_batch", &Gempyre::Ui::beginBatch)
        .def("end_batch", &Gempyre::Ui::endBatch)
        .def("hold_timers", &Gempyre::Ui::holdTimers)
        .def("is_hold", &Gempyre::Ui::isHold)
        .def("device_pixel_ratio", &Gempyre::Ui::devicePixelRatio)
            ;

        py::class_<Gempyre::CanvasElement, Gempyre::Element>(m, "CanvasElement")
                .def(py::init<const Gempyre::CanvasElement&>())
                .def(py::init<Gempyre::Ui&, const std::string&>())
                .def(py::init<Gempyre::Ui&, const std::string&, const Gempyre::Element&>())
                .def("add_image", [](Gempyre::CanvasElement* canvas, const std::string& url, const std::function<void (const std::string&)> loaded = nullptr){
                    return canvas->addImage(url, [loaded](const std::string& id) {if(loaded) {py::gil_scoped_acquire acquire; loaded(id);}});})
                .def("add_images", [](Gempyre::CanvasElement* canvas, const std::vector<std::string> urls, const std::function<void (const std::vector<std::string>&)>& loaded = nullptr) {
                    return canvas->addImages(urls, [loaded](const std::vector<std::string>& vec) {if(loaded) {py::gil_scoped_acquire acquire; loaded(vec);}});})
                .def("paint_image", [](Gempyre::CanvasElement* el, const std::string& imageId, int x, int y, const RectF& clippingRect) {
                    el->paintImage(imageId, x, y, clippingRect);
                    }, py::arg("imageId"), py::arg("x"), py::arg("y"), py::arg("clippingRect") = RectF{0, 0, 0, 0})
                .def("paint_image_rect", [](Gempyre::CanvasElement* el, const std::string& imageId, const RectF& targetRect, const RectF& clippingRect) {
                    el->paintImage(imageId, targetRect, clippingRect);
                    }, py::arg("imageId"), py::arg("targetRect"), py::arg("clippingRect") = RectF{0, 0, 0, 0})
                .def("draw_commands", py::overload_cast<const Gempyre::CanvasElement::CommandList&>(&Gempyre::CanvasElement::draw, py::const_))
                .def("draw_frame", py::overload_cast<const Gempyre::FrameComposer&>(&Gempyre::CanvasElement::draw, py::const_))
                .def("erase", &Gempyre::CanvasElement::erase, py::arg("resized") = false)
                .def("draw_completed", [](Gempyre::CanvasElement* el, std::function<void ()> drawCallback = nullptr) {
                    el->drawCompleted(drawCallback ? [&drawCallback]() {
                        py::gil_scoped_acquire acquire;
                        drawCallback();
                    } : drawCallback);
                })
                ;
        m.def("color_rgba_clamped", &Gempyre::Color::rgbaClamped, py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF);
        m.def("color_rgba", py::overload_cast<uint32_t, uint32_t, uint32_t, uint32_t>(&Gempyre::Color::rgba), py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF);
        m.def("color_rgba_string", py::overload_cast<uint32_t>(&Gempyre::Color::rgba));
        m.def("color_rgb_string", py::overload_cast<uint32_t>(&Gempyre::Color::rgb));
        m.def("color_r", &Gempyre::Color::r);
        m.def("color_g", &Gempyre::Color::g);
        m.def("color_b", &Gempyre::Color::b);
        m.def("color_alpha", &Gempyre::Color::alpha)
        ;

        py::class_<Gempyre::Graphics>(m, "Graphics")
                .def(py::init<Gempyre::CanvasElement&, int, int>())
                //There is no makeCanvas... .def(py::init<Gempyre::CanvasElement&>())
                .def(py::init<const Gempyre::Graphics&>())
                .def("create", &Gempyre::Graphics::create)
                .def("clone", &Gempyre::Graphics::clone)
                .def_static("pix", &Gempyre::Graphics::pix, py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF)
                .def_property_readonly_static("Black", [](py::object){return Gempyre::Graphics::Black;})
                .def_property_readonly_static("White", [](py::object){return Gempyre::Graphics::White;})
                .def_property_readonly_static("Black", [](py::object){return Gempyre::Graphics::Black;})
                .def_property_readonly_static("Red", [](py::object){return Gempyre::Graphics::Red;})
                .def_property_readonly_static("Green", [](py::object){return Gempyre::Graphics::Green;})
                .def_property_readonly_static("Blue", [](py::object){return Gempyre::Graphics::Blue;})
                .def("set_pixel", &Gempyre::Graphics::setPixel)
                .def("set_alpha", &Gempyre::Graphics::setAlpha)
                .def("width", &Gempyre::Graphics::width)
                .def("height", &Gempyre::Graphics::height)
                .def("draw_rect", [](Gempyre::Graphics* g, const RectF& r, Gempyre::Color::type c) {g->drawRect(r, c);})
                .def("merge", &Gempyre::Graphics::merge)
                .def("swap", &Gempyre::Graphics::swap)
                .def("update", &Gempyre::Graphics::update)
                ;

        py::class_<Gempyre::FrameComposer>(m, "FrameComposer")
                .def(py::init<>())
                .def(py::init<Gempyre::CanvasElement::CommandList&>())
                .def(py::init<const Gempyre::FrameComposer&>())
                .def("stroke_rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->strokeRect(r);})
                .def("clear_rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->clearRect(r);})
                .def("fill_rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->fillRect(r);})
                .def("fill_text", &Gempyre::FrameComposer::fillText)
                .def("stroke_text", &Gempyre::FrameComposer::strokeText)
                .def("arc", &Gempyre::FrameComposer::arc)
                .def("ellipse", &Gempyre::FrameComposer::ellipse)
                .def("begin_path", &Gempyre::FrameComposer::beginPath)
                .def("close_path", &Gempyre::FrameComposer::closePath)
                .def("line_to", &Gempyre::FrameComposer::lineTo)
                .def("move_to", &Gempyre::FrameComposer::moveTo)
                .def("bezier_curve_to", &Gempyre::FrameComposer::bezierCurveTo)
                .def("quadratic_curve_to", &Gempyre::FrameComposer::quadraticCurveTo)
                .def("arc_to", &Gempyre::FrameComposer::arcTo)
                .def("rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->rect(r);})
                .def("stroke", &Gempyre::FrameComposer::stroke)
                .def("fill", &Gempyre::FrameComposer::fill)
                .def("fill_style", &Gempyre::FrameComposer::fillStyle)
                .def("stroke_style", &Gempyre::FrameComposer::strokeStyle)
                .def("line_width", &Gempyre::FrameComposer::lineWidth)
                .def("font", &Gempyre::FrameComposer::font)
                .def("text_align", &Gempyre::FrameComposer::textAlign)
                .def("save", &Gempyre::FrameComposer::save)
                .def("restore", &Gempyre::FrameComposer::restore)
                .def("rotate", &Gempyre::FrameComposer::rotate)
                .def("translate", &Gempyre::FrameComposer::translate)
                .def("scale", &Gempyre::FrameComposer::scale)
                .def("draw_image", py::overload_cast<const std::string&, double, double>(&Gempyre::FrameComposer::drawImage))
                .def("draw_image_rect", [](Gempyre::FrameComposer* fc, const std::string& id, const RectF& r) {fc->drawImage(id, r);})
                .def("draw_image_clip", [](Gempyre::FrameComposer* fc, const std::string& id, const RectF& c, const RectF& r){fc->drawImage(id, c, r);})
                .def("composed", &Gempyre::FrameComposer::composed)
                ;
    
        py::class_<GempyreClient::Dialog<Gempyre::Ui>>(m, "Dialog")
            .def(py::init<Gempyre::Ui&>())
            
            .def("open_file_dialog", [](GempyreClient::Dialog<Gempyre::Ui>* dlg, const std::string& caption, const std::string& root, const std::vector<std::tuple<std::string, std::vector<std::string>>>& filter = {})->std::optional<std::string> {
                py::gil_scoped_acquire acquire;
                return dlg->openFileDialog(caption, root, filter);    
            }, py::arg("caption")="", py::arg("root")="", py::arg("filter")=GempyreClient::Dialog<Gempyre::Ui>::Filter())
            
            .def("open_files_dialog", [](GempyreClient::Dialog<Gempyre::Ui>* dlg, const std::string& caption, const std::string& root, const std::vector<std::tuple<std::string, std::vector<std::string>>>& filter = {})->std::optional<std::vector<std::string>> {
                py::gil_scoped_acquire acquire;
                return dlg->openFilesDialog(caption, root, filter);    
            }, py::arg("caption")="", py::arg("root")="", py::arg("filter")=GempyreClient::Dialog<Gempyre::Ui>::Filter())
            
            .def("open_dir_dialog", [](GempyreClient::Dialog<Gempyre::Ui>* dlg, const std::string& caption, const std::string& root)->std::optional<std::string> {
                py::gil_scoped_acquire acquire;
                return dlg->openDirDialog(caption, root);    
            }, py::arg("caption")="", py::arg("root")="")
            
            .def("save_file_dialog", [](GempyreClient::Dialog<Gempyre::Ui>* dlg, const std::string& caption, const std::string& root, const std::vector<std::tuple<std::string, std::vector<std::string>>>& filter = {})->std::optional<std::string> {
                py::gil_scoped_acquire acquire;
                return dlg->saveFileDialog(caption, root, filter);    
            }, py::arg("caption")="", py::arg("root")="", py::arg("filter")=GempyreClient::Dialog<Gempyre::Ui>::Filter())
            ;
}
