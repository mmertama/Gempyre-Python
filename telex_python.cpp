#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <telex.h>
#include <telex_graphics.h>
#include <../src/json.h> //as pybind11 wont support std::any we convert them to string using this internal class, sorry


namespace py = pybind11;


class RectF {
public:
    double x, y, width, height;
    operator Telex::Element::Rect() const {
        return Telex::Element::Rect{static_cast<int>(x), static_cast<int>(y), static_cast<int>(width), static_cast<int>(height)};
    }
};



static RectF rectF(const Telex::Element::Rect& r) {
    return RectF{ static_cast<double>(r.x), static_cast<double>(r.y), static_cast<double>(r.width), static_cast<double>(r.height) };
}


static  std::optional<std::string> TelexExtension(Telex::Ui* ui, const std::string& callId, const std::unordered_map<std::string, std::string>& parameters) {
    std::unordered_map<std::string, std::any> params;
    for(const auto& [k, v] : parameters) {
        const auto any = Telex::toAny(v); // Not sure how well tested
        if(any)
            params.emplace(k, any);
         else {
            std::cerr << "Cannot make " << k << "->" << v << " to any" << std::endl;
            return std::nullopt;
        }
    }
    std::optional<std::any> ext =  ui->extension(callId, params);
    return ext ? Telex::toString(*ext) : std::nullopt;
}



PYBIND11_MODULE(Telex, m) {
    m.def("set_debug", &Telex::setDebug);
    m.def("version", &Telex::version);

    py::class_<Telex::Event>(m, "Event")
            .def_readonly("element", &Telex::Event::element)
            .def_readonly("properties", &Telex::Event::properties)
            ;

    py::class_<RectF>(m, "Rect")
            .def(py::init<>())
            .def(py::init<double, double, double, double>())
            .def_readwrite("x", &RectF::x)
            .def_readwrite("y", &RectF::y)
            .def_readwrite("width", &RectF::width)
            .def_readwrite("height", &RectF::height)
            ;

    py::class_<Telex::Element>(m, "Element")
            .def(py::init<const Telex::Element&>())
            .def(py::init<Telex::Ui&, const std::string&>())
            .def(py::init<Telex::Ui&, const std::string, const std::string&, const Telex::Element&>())
            .def(py::init<Telex::Ui&, const std::string&, const Telex::Element&>())
            .def("ui", py::overload_cast<>(&Telex::Element::ui, py::const_))
            .def("ui", py::overload_cast<>(&Telex::Element::ui))
            .def("id", &Telex::Element::id)
            .def("subscribe", [](Telex::Element* el, const std::string& name, std::function<void(const Telex::Event& ev)> handler, const std::vector<std::string>& properties, const std::chrono::milliseconds& throttle = 0ms) {
                 return el->subscribe(name, [handler](const Telex::Event& ev){py::gil_scoped_acquire acquire; handler(ev);}, properties, throttle);
                }, py::arg("name"), py::arg("handler"), py::arg("properties") = std::vector<std::string>{}, py::arg("throttle") = 0ms)
            .def("set_html", &Telex::Element::setHTML)
            .def("set_attribute", &Telex::Element::setAttribute, py::arg("attr"), py::arg("value") = "")
            .def("remove_attribute", &Telex::Element::removeAttribute)
            .def("set_style", &Telex::Element::setStyle)
            .def("remove_style", &Telex::Element::removeStyle)
            .def("styles", &Telex::Element::styles)
            .def("attributes", &Telex::Element::attributes)
            .def("children", &Telex::Element::children)
            .def("values", &Telex::Element::values)
            .def("html", &Telex::Element::html)
            .def("remove", &Telex::Element::remove)
            .def("type", &Telex::Element::type)
            .def("rect", [](Telex::Element* el) {
                const auto r = el->rect();
                return r ? std::make_optional<RectF>(::rectF(*r)) :  std::nullopt;
                })
//            .def("rect", &Telex::Element::rect)
            ;
    py::class_<Telex::Ui>(m, "Ui")
       // Should I comment these out as using them is confusing due browser security concerns
        .def(py::init<const std::string&, const std::string&, const std::string&, unsigned short, const std::string& >(),
             py::arg("indexHtml"),
             py::arg("browser"),
             py::arg("extraParams") = "",
             py::arg("port") = Telex::Ui::UseDefaultPort,
             py::arg("root") = Telex::Ui::UseDefaultRoot
             )
        .def(py::init<const std::string&, unsigned short, const std::string& >(),
                 py::arg("indexHtml"),
                 py::arg("port") = Telex::Ui::UseDefaultPort,
                 py::arg("root") = Telex::Ui::UseDefaultRoot
                 )
        .def(py::init<const Telex::Ui::Filemap&, const std::string&, const std::string&, const std::string&, unsigned short, const std::string& >(),
             py::arg("filemap"),
             py::arg("indexHtml"),
             py::arg("browser"),
             py::arg("extraParams") = "",
             py::arg("port") = Telex::Ui::UseDefaultPort,
             py::arg("root") = Telex::Ui::UseDefaultRoot
             )
        .def(py::init<const Telex::Ui::Filemap&, const std::string&, unsigned short, const std::string& >(),
             py::arg("filemap"),
             py::arg("indexHtml"),
             py::arg("port") = Telex::Ui::UseDefaultPort,
             py::arg("root") = Telex::Ui::UseDefaultRoot
            )
        .def_readonly_static("UseDefaultPort", &Telex::Ui::UseDefaultPort)
        .def_readonly_static("UseDefaultRoot", &Telex::Ui::UseDefaultRoot)
        .def("run", &Telex::Ui::run, py::call_guard<py::gil_scoped_release>())
        .def("exit", &Telex::Ui::exit)
        .def("close", &Telex::Ui::close)
        .def("on_exit", [](Telex::Ui* ui, std::function<void ()> onExitFunction = nullptr)->Telex::Ui& {
            return ui->onExit(onExitFunction ? [onExitFunction]() {py::gil_scoped_acquire acquire; return onExitFunction(); } :
                static_cast<decltype(onExitFunction)>(nullptr)); })
        .def("on_reload", [](Telex::Ui* ui, std::function<void ()> onReloadFunction = nullptr)->Telex::Ui& {
        return ui->onReload(onReloadFunction ? [onReloadFunction]() {py::gil_scoped_acquire acquire; return onReloadFunction(); } :
            static_cast<decltype(onReloadFunction)>(nullptr)); })
        .def("on_open", [](Telex::Ui* ui, std::function<void ()> onOpenFunction = nullptr)->Telex::Ui& {
        return ui->onOpen(onOpenFunction ? [onOpenFunction]() {py::gil_scoped_acquire acquire; return onOpenFunction(); } :
            static_cast<decltype(onOpenFunction)>(nullptr)); })
        .def("on_error", [](Telex::Ui* ui, std::function<void (const std::string& element, const std::string& info)> onErrorFunction = nullptr)->Telex::Ui& {
        return ui->onError(onErrorFunction ? [onErrorFunction](const std::string& element, const std::string& info) {py::gil_scoped_acquire acquire; return onErrorFunction(element, info); } :
            static_cast<decltype(onErrorFunction)>(nullptr)); })
        .def("set_logging", &Telex::Ui::setLogging)
        .def("eval", &Telex::Ui::eval)
        .def("debug", &Telex::Ui::debug)
        .def("alert", &Telex::Ui::alert)
        .def("open", &Telex::Ui::open, py::arg("url"), py::arg("name") = "")
        .def("start_timer", [](Telex::Ui* ui, const std::chrono::milliseconds& ms, bool b, const std::function<void ()>& f) {
            return ui->startTimer(ms, b, [f](){py::gil_scoped_acquire acquire; f();});})
        // When wrapping in fp (to enable GIL), there is no need: py::overload_cast<const std::chrono::milliseconds&, bool, const std::function<void (Telex::Ui::TimerId)>&>(&Telex::Ui::startTimer)
        .def("start_timer", [](Telex::Ui* ui, const std::chrono::milliseconds& ms, bool b, const std::function<void (Telex::Ui::TimerId)>& f) {
            return ui->startTimer(ms, b, [f](Telex::Ui::TimerId tid){py::gil_scoped_acquire acquire; f(tid);});})
        .def("stop_timer", &Telex::Ui::stopTimer)
        .def("root", &Telex::Ui::root)
        .def("address_of", &Telex::Ui::addressOf)
        .def("by_class", &Telex::Ui::byClass)
        .def("by_name", &Telex::Ui::byName)
        .def("ping", &Telex::Ui::ping)
         .def("extension", &TelexExtension)
        .def("resource", &Telex::Ui::resource)
        .def("add_file", &Telex::Ui::addFile)
        .def("begin_batch", &Telex::Ui::beginBatch)
        .def("end_batch", &Telex::Ui::endBatch)
            ;

        py::class_<Telex::CanvasElement, Telex::Element>(m, "CanvasElement")
                .def(py::init<const Telex::CanvasElement&>())
                .def(py::init<Telex::Ui&, const std::string&>())
                .def(py::init<Telex::Ui&, const std::string&, const Telex::Element&>())
                .def("add_image", [](Telex::CanvasElement* canvas, const std::string& url, const std::function<void (const std::string&)> loaded = nullptr){
                    return canvas->addImage(url, [loaded](const std::string& id) {if(loaded) {py::gil_scoped_acquire acquire; loaded(id);}});})
                .def("add_images", [](Telex::CanvasElement* canvas, const std::vector<std::string> urls, const std::function<void (const std::vector<std::string>&)>& loaded = nullptr) {
                    return canvas->addImages(urls, [loaded](const std::vector<std::string>& vec) {if(loaded) {py::gil_scoped_acquire acquire; loaded(vec);}});})
                .def("paint_image", [](Telex::CanvasElement* el, const std::string& imageId, int x, int y, const RectF& clippingRect) {
                    el->paintImage(imageId, x, y, clippingRect);
                    }, py::arg("imageId"), py::arg("x"), py::arg("y"), py::arg("clippingRect") = RectF{0, 0, 0, 0})
                .def("paint_image_rect", [](Telex::CanvasElement* el, const std::string& imageId, const RectF& targetRect, const RectF& clippingRect) {
                    el->paintImage(imageId, targetRect, clippingRect);
                    }, py::arg("imageId"), py::arg("targetRect"), py::arg("clippingRect") = RectF{0, 0, 0, 0})
                .def("draw_commands", py::overload_cast<const Telex::CanvasElement::CommandList&>(&Telex::CanvasElement::draw))
                .def("draw_frame", py::overload_cast<const Telex::FrameComposer&>(&Telex::CanvasElement::draw))
                .def("erase", &Telex::CanvasElement::erase, py::arg("resized") = false)
                ;
        m.def("color_rgba_clamped", &Telex::Color::rgbaClamped);
        m.def("color_rgba", &Telex::Color::rgba);
        m.def("color_r", &Telex::Color::r);
        m.def("color_g", &Telex::Color::g);
        m.def("color_b", &Telex::Color::b);
        m.def("color_alpha", &Telex::Color::alpha)
        ;

        py::class_<Telex::Graphics>(m, "Graphics")
                .def(py::init<Telex::CanvasElement&, int, int>())
                .def(py::init<Telex::CanvasElement&>())
                .def(py::init<const Telex::Graphics&>())
                .def("create", &Telex::Graphics::create)
                .def("clone", &Telex::Graphics::clone)
                .def_static("pix", &Telex::Graphics::pix, py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF)
                .def_property_readonly_static("Black", [](){return Telex::Graphics::Black;})
                .def_property_readonly_static("White", [](){return Telex::Graphics::White;})
                .def_property_readonly_static("Black", [](){return Telex::Graphics::Black;})
                .def_property_readonly_static("Red", [](){return Telex::Graphics::Red;})
                .def_property_readonly_static("Green", [](){return Telex::Graphics::Green;})
                .def_property_readonly_static("Blue", [](){return Telex::Graphics::Blue;})
                .def("set_pixel", &Telex::Graphics::setPixel)
                .def("set_alpha", &Telex::Graphics::setAlpha)
                .def("width", &Telex::Graphics::width)
                .def("height", &Telex::Graphics::height)
                .def("draw_rect", [](Telex::Graphics* g, const RectF& r, Telex::Color::type c) {g->drawRect(r, c);})
                .def("merge", &Telex::Graphics::merge)
                .def("swap", &Telex::Graphics::swap)
                .def("update", &Telex::Graphics::update)
                ;

        py::class_<Telex::FrameComposer>(m, "FrameComposer")
                .def(py::init<>())
                .def(py::init<Telex::CanvasElement::CommandList&>())
                .def(py::init<const Telex::FrameComposer&>())
                .def("stroke_rect", [](Telex::FrameComposer* fc, const RectF& r) {fc->strokeRect(r);})
                .def("clear_rect", [](Telex::FrameComposer* fc, const RectF& r) {fc->clearRect(r);})
                .def("fill_rect", [](Telex::FrameComposer* fc, const RectF& r) {fc->fillRect(r);})
                .def("fill_text", &Telex::FrameComposer::fillText)
                .def("stroke_text", &Telex::FrameComposer::strokeText)
                .def("arc", &Telex::FrameComposer::arc)
                .def("ellipse", &Telex::FrameComposer::ellipse)
                .def("begin_path", &Telex::FrameComposer::beginPath)
                .def("close_path", &Telex::FrameComposer::closePath)
                .def("line_to", &Telex::FrameComposer::lineTo)
                .def("move_to", &Telex::FrameComposer::moveTo)
                .def("bezier_curve_to", &Telex::FrameComposer::bezierCurveTo)
                .def("quadratic_curve_to", &Telex::FrameComposer::quadraticCurveTo)
                .def("arc_to", &Telex::FrameComposer::arcTo)
                .def("rect", [](Telex::FrameComposer* fc, const RectF& r) {fc->rect(r);})
                .def("stroke", &Telex::FrameComposer::stroke)
                .def("fill", &Telex::FrameComposer::fill)
                .def("fill_style", &Telex::FrameComposer::fillStyle)
                .def("stroke_style", &Telex::FrameComposer::strokeStyle)
                .def("line_width", &Telex::FrameComposer::lineWidth)
                .def("font", &Telex::FrameComposer::font)
                .def("text_align", &Telex::FrameComposer::textAlign)
                .def("save", &Telex::FrameComposer::save)
                .def("restore", &Telex::FrameComposer::restore)
                .def("rotate", &Telex::FrameComposer::rotate)
                .def("translate", &Telex::FrameComposer::translate)
                .def("scale", &Telex::FrameComposer::scale)
                .def("draw_image", py::overload_cast<const std::string&, double, double>(&Telex::FrameComposer::drawImage))
                .def("draw_image_rect", [](Telex::FrameComposer* fc, const std::string& id, const RectF& r) {fc->drawImage(id, r);})
                .def("draw_image_clip", [](Telex::FrameComposer* fc, const std::string& id, const RectF& c, const RectF& r){fc->drawImage(id, c, r);})
                .def("composed", &Telex::FrameComposer::composed)
                ;
}
