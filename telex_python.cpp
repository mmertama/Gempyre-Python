#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <telex.h>

namespace py = pybind11;

PYBIND11_MODULE(Telex, m) {
    m.def("set_debug", &Telex::setDebug);
    m.def("version", &Telex::version);
    py::class_<Telex::Event>(m, "Event")
            .def_readonly("element", &Telex::Event::element)
            .def_readonly("properties", &Telex::Event::properties)
            ;
    py::class_<Telex::Element>(m, "Element")
            .def(py::init<const Telex::Element&>())
            .def(py::init<Telex::Ui&, const std::string&>())
            .def(py::init<Telex::Ui&, const std::string, const std::string&, const Telex::Element&>())
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
}
