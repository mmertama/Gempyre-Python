#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <telex.h>
#include <telex_graphics.h>

namespace py = pybind11;

PYBIND11_MODULE(Telex, m) {
    m.def("set_debug", &Telex::setDebug);
    m.def("version", &Telex::version);

    py::class_<Telex::Event>(m, "Event")
            .def_readonly("element", &Telex::Event::element)
            .def_readonly("properties", &Telex::Event::properties)
            ;
    py::class_<Telex::Element::Rect>(m, "Rect")
            .def_readwrite("x", &Telex::Element::Rect::x)
            .def_readwrite("y", &Telex::Element::Rect::y)
            .def_readwrite("width", &Telex::Element::Rect::width)
            .def_readwrite("height", &Telex::Element::Rect::height)
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
            .def("set_attribute", &Telex::Element::setAttribute)
            .def("attributes", &Telex::Element::attributes)
            .def("children", &Telex::Element::children)
            .def("values", &Telex::Element::values)
            .def("html", &Telex::Element::html)
            .def("remove", &Telex::Element::remove)
            .def("type", &Telex::Element::type)
            .def("rect", &Telex::Element::rect)
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
        .def("extension", &Telex::Ui::extension)
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
                .def("paint_image", py::overload_cast<const std::string&, int, int, const Telex::Element::Rect&>(&Telex::CanvasElement::paintImage), py::arg("imageId"), py::arg("x"), py::arg("y"), py::arg("clippingRect") = Telex::Element::Rect{0, 0, 0, 0})
                .def("paint_image_rect", py::overload_cast<const std::string&, const Telex::Element::Rect&, const Telex::Element::Rect&>(&Telex::CanvasElement::paintImage), py::arg("imageId"), py::arg("targetRect"), py::arg("clippingRect") = Telex::Element::Rect{0, 0, 0, 0})
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
                .def("draw_rect", &Telex::Graphics::drawRect)
                .def("merge", &Telex::Graphics::merge)
                .def("swap", &Telex::Graphics::swap)
                .def("update", &Telex::Graphics::update)
                ;
}
